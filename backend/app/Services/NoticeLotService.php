<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\NoticeLot;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;

class NoticeLotService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, NoticeLot>
     */
    public function getLots(array $filters = []): LengthAwarePaginator
    {
        $query = NoticeLot::query()->with([
            'procedure.buyer',
            'procedure.cpvCode',
            'procedure.nutCode',
            'procedure.procedureType',
            'procedure.contractNature',
            'cpvCode',
            'nutCode',
            'durationUnit',
            'awardCriterionType',
            'reservedExecutionType',
            'reservedParticipationType',
            'einvoicingPermission',
            'variantsApplicability',
        ]);

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('lot_reference', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('title', 'like', '%' . $filters['search'] . '%');
            });
        }

        foreach (['procedure_id', 'main_cpv', 'nuts_code', 'eu_funded'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        return $query
            ->orderByDesc('created_at')
            ->orderByDesc('id')
            ->paginate(
                (int) ($filters['per_page'] ?? 15),
                ['*'],
                'page',
                (int) ($filters['page'] ?? 1),
            );
    }
}
