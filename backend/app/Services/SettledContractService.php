<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Organization;
use App\Models\SettledContract;
use Carbon\Carbon;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Cache;

class SettledContractService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, SettledContract>
     */
    public function getSettledContracts(array $filters = []): LengthAwarePaginator
    {
        $query = SettledContract::query()->with([
            'notice.procedure.buyer',
            'notice.formType',
            'notice.noticeType',
        ]);

        if (! empty($filters['search'])) {
            $term = '%' . addcslashes((string) $filters['search'], '%_\\') . '%';

            $query->where(function (Builder $query) use ($term): void {
                $query->where('title', 'ilike', $term)
                    ->orWhere('contract_number', 'ilike', $term)
                    ->orWhere('contract_ref', 'ilike', $term)
                    ->orWhere('notice_id', 'ilike', $term);
            });
        }

        if (isset($filters['notice_id'])) {
            $query->where('notice_id', $filters['notice_id']);
        }

        if (isset($filters['procedure_id'])) {
            $query->forProcedure((int) $filters['procedure_id']);
        }

        if (isset($filters['buyer_id'])) {
            $query->forBuyer((int) $filters['buyer_id']);
        }

        if (isset($filters['conclusion_from'])) {
            $query->whereDate('conclusion_date', '>=', $filters['conclusion_from']);
        }

        if (isset($filters['conclusion_to'])) {
            $query->whereDate('conclusion_date', '<=', $filters['conclusion_to']);
        }

        if (isset($filters['has_url'])) {
            $this->flag($filters['has_url'])
                ? $query->withContractUrl()
                : $query->where(fn(Builder $q) => $q->whereNull('contract_url')->orWhere('contract_url', ''));
        }

        if (isset($filters['has_tenders'])) {
            $this->flag($filters['has_tenders'])
                ? $query->has('tenders')
                : $query->doesntHave('tenders');
        }

        if (isset($filters['only_current']) && $this->flag($filters['only_current'])) {
            $query->current();
        }

        $sort = $filters['sort'] ?? 'conclusion_date';
        $direction = ($filters['direction'] ?? 'desc') === 'asc' ? 'asc' : 'desc';

        return $query
            ->orderBy($sort, $direction)
            ->orderByDesc('id')
            ->paginate(
                (int) ($filters['per_page'] ?? 15),
                ['*'],
                'page',
                (int) ($filters['page'] ?? 1),
            );
    }

    public function getSettledContract(SettledContract $settledContract): SettledContract
    {
        return $settledContract->load([
            'notice.procedure.buyer',
            'notice.procedure.cpvCode',
            'notice.procedure.nutCode',
            'notice.procedure.procedureType',
            'notice.procedure.contractNature',
            'notice.formType',
            'notice.noticeType',
            'notice.legalBasis',
            'tenders',
        ]);
    }

    /** @param array<string, mixed> $filters
     * @return array<string, mixed>
     */
    public function getKpis(array $filters = []): array
    {
        $filters = array_intersect_key($filters, ['buyer_id' => true]);
        $key = 'settled_contracts.kpis.' . md5(json_encode($filters, JSON_THROW_ON_ERROR));

        return Cache::remember($key, now()->addMinutes(15), fn(): array => [
            'contracts' => $this->contractStats($filters),
            'coverage' => $this->coverageStats($filters),
            'reach' => $this->reachStats($filters),
            'monthly' => $this->monthlyTrend($filters),
        ]);
    }

    /** @param array<string, mixed> $filters
     * @return Builder<SettledContract>
     */
    private function baseQuery(array $filters): Builder
    {
        return SettledContract::query()
            ->current()
            ->when(
                $filters['buyer_id'] ?? null,
                fn(Builder $q, $buyerId) => $q->forBuyer((int) $buyerId),
            );
    }

    /** @param array<string, mixed> $filters */
    private function contractStats(array $filters): array
    {
        $now = now();

        $last30 = $this->baseQuery($filters)->concludedBetween($now->copy()->subDays(30))->count();
        $prev30 = $this->baseQuery($filters)
            ->concludedBetween($now->copy()->subDays(60), $now->copy()->subDays(30))
            ->count();

        return [
            'total' => $this->baseQuery($filters)->count(),
            'last_30' => $last30,
            'prev_30' => $prev30,
            'change_pct' => $prev30 > 0 ? round(($last30 - $prev30) / $prev30 * 100, 1) : null,
            'latest_conclusion' => $this->baseQuery($filters)->max('conclusion_date'),
        ];
    }

    /** @param array<string, mixed> $filters */
    private function coverageStats(array $filters): array
    {
        $total = $this->baseQuery($filters)->count();
        $withUrl = $this->baseQuery($filters)->withContractUrl()->count();
        $withTenders = $this->baseQuery($filters)->has('tenders')->count();

        return [
            'with_url' => $withUrl,
            'with_url_pct' => $total > 0 ? round($withUrl / $total * 100, 1) : 0.0,
            'with_tenders' => $withTenders,
            'with_tenders_pct' => $total > 0 ? round($withTenders / $total * 100, 1) : 0.0,
            'with_tender_refs' => $this->baseQuery($filters)->whereNotNull('tender_refs')->count(),
        ];
    }

    /** @param array<string, mixed> $filters */
    private function reachStats(array $filters): array
    {
        return [
            'notices' => $this->baseQuery($filters)->distinct()->count('notice_record_id'),
            'buyers' => Organization::query()
                ->whereHas('procedures.notices', fn(Builder $q) => $q->current()->has('settledContracts'))
                ->when($filters['buyer_id'] ?? null, fn(Builder $q, $id) => $q->whereKey($id))
                ->count(),
        ];
    }

    /**
     * Contracts concluded per month for the last 12 months (PostgreSQL).
     *
     * @param array<string, mixed> $filters
     *
     * @return list<array{month: string, total: int}>
     */
    private function monthlyTrend(array $filters): array
    {
        return $this->baseQuery($filters)
            ->where('conclusion_date', '>=', now()->subMonths(11)->startOfMonth())
            ->selectRaw("DATE_TRUNC('month', conclusion_date) AS month, COUNT(*) AS total")
            ->groupBy('month')
            ->orderBy('month')
            ->get()
            ->map(fn($row): array => [
                'month' => Carbon::parse($row->month)->format('Y-m'),
                'total' => (int) $row->total,
            ])
            ->all();
    }

    private function flag(mixed $value): bool
    {
        return filter_var($value, FILTER_VALIDATE_BOOLEAN);
    }
}
