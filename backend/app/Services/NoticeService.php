<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\LotResult;
use App\Models\LotResultSubmissionStat;
use App\Models\Notice;
use App\Models\NoticeLot;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Cache;

class NoticeService
{
    private const OUTCOME_AWARDED = 'selec-w';

    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, Notice>
     */
    public function getNotices(array $filters = []): LengthAwarePaginator
    {
        $query = Notice::query()->with([
            'procedure.buyer',
            'procedure.cpvCode',
            'procedure.nutCode',
            'procedure.procedureType',
            'procedure.contractNature',
            'formType',
            'noticeType',
            'legalBasis',
        ]);

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('notice_id', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('title', 'like', '%' . $filters['search'] . '%');
            });
        }

        foreach (['notice_type', 'form_type'] as $field) {
            if (! empty($filters[$field])) {
                $query->whereIn($field, $filters[$field]);
            }
        }

        if (isset($filters['procedure_id'])) {
            $query->where('procedure_id', $filters['procedure_id']);
        }

        if (isset($filters['is_latest'])) {
            $query->where('is_latest', $filters['is_latest']);
        }

        if (isset($filters['published_from'])) {
            $query->whereDate('published_at', '>=', $filters['published_from']);
        }

        if (isset($filters['published_to'])) {
            $query->whereDate('published_at', '<=', $filters['published_to']);
        }

        $sort = $filters['sort'] ?? 'created_at';
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

    public function getKpis(): array
    {
        return Cache::remember('notices.kpis', now()->addMinutes(15), fn(): array => [
            'notices' => $this->noticeStats(),
            'lots' => $this->lotStats(),
            'competition' => $this->competitionStats(),
        ]);
    }

    private function noticeStats(): array
    {
        $now = now();

        return [
            'total' => Notice::current()->count(),
            'last_30' => Notice::current()->publishedBetween($now->copy()->subDays(30))->count(),
            'prev_30' => Notice::current()->publishedBetween($now->copy()->subDays(60), $now->copy()->subDays(30))->count(),
        ];
    }

    private function lotStats(): array
    {
        return [
            'lots' => LotResult::current()->count(),
            'total_value' => (float) NoticeLot::current()->inEur()->sum('estimated_value'),
            'with_outcome' => LotResult::current()->withOutcome()->count(),
            'awarded' => LotResult::current()->awarded()->count(),
            'eu_known' => NoticeLot::current()->whereNotNull('eu_funded')->count(),
            'eu_funded' => NoticeLot::current()->euFunded()->count(),
        ];
    }

    private function competitionStats(): array
    {
        $statsQuery = LotResultSubmissionStat::query()
            ->where('category_code', LotResult::STAT_TOTAL_TENDERS)
            ->whereNotNull('count')
            ->whereHas('lotResult', fn(Builder $q) => $q->current());

        return [
            'lots' => (clone $statsQuery)->count(),
            'avg_bids' => round((float) (clone $statsQuery)->avg('count'), 1),
            'median_bids' => round((float) (clone $statsQuery)
                ->selectRaw('PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY count) AS median')
                ->value('median'), 1),
            'single_bid' => (clone $statsQuery)->where('count', 1)->count(),
        ];
    }
}
