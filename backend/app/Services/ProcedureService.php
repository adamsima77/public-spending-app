<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Procedure;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\CursorPaginator;

class ProcedureService
{
    /** @param array<string, mixed> $filters
     * @return CursorPaginator<int, Procedure>
     */
    public function getAllProcedures(array $filters = []): CursorPaginator
    {
        $query = Procedure::query()->with([
            'buyer.nutCode',
            'buyer.companySize',
            'cpvCode',
            'nutCode',
            'procedureType',
            'contractNature',
        ]);

        foreach (['procedure_type', 'buyer_id', 'main_cpv', 'nuts_code'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('procedure_reference', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('procedure_identifier', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('title', 'like', '%' . $filters['search'] . '%');
            });
        }

        return $query
            ->orderByDesc('created_at')
            ->orderByDesc('id')
            ->cursorPaginate((int) ($filters['per_page'] ?? 15));
    }
}
