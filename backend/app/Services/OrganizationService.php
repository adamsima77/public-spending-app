<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\LotSupplier;
use App\Models\Organization;
use App\Models\Procedure;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\DB;

class OrganizationService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, Organization>
     */
    public function getAllOrganizations(array $filters = []): LengthAwarePaginator
    {
        $query = Organization::query()->with(['nutCode', 'companySize']);

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('name', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('cin', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('tin', 'like', '%' . $filters['search'] . '%');
            });
        }

        if (! empty($filters['company_size']) || ! empty($filters['without_company_size'])) {
            $query->where(function (Builder $q) use ($filters): void {
                if (! empty($filters['company_size'])) {
                    $companySizes = $filters['company_size'];

                    if (in_array('sme', $companySizes, true)) {
                        $companySizes = array_values(array_unique([
                            ...$companySizes,
                            'micro',
                            'small',
                            'medium',
                        ]));
                    }

                    $q->whereIn('company_size', $companySizes);
                }

                if (! empty($filters['without_company_size'])) {
                    $q->orWhereNull('company_size');
                }
            });
        }

        if (! empty($filters['country'])) {
            $query->whereIn('country', $filters['country']);
        }

        if (! empty($filters['role'])) {
            $buyerIds = Procedure::query()
                ->select('buyer_id')
                ->whereNotNull('buyer_id');
            $supplierIds = LotSupplier::query()->select('organization_id');
            $tenderOrganizationIds = DB::table('lot_tender_organizations')
                ->select('organization_id');

            $query->where(function (Builder $q) use (
                $filters,
                $buyerIds,
                $supplierIds,
                $tenderOrganizationIds,
            ): void {
                foreach ($filters['role'] as $role) {
                    $roleQuery = match ($role) {
                        'buyer' => fn(Builder $roleQuery) => $roleQuery->whereIn('id', $buyerIds),
                        'supplier' => fn(Builder $roleQuery) => $roleQuery->whereIn('id', $supplierIds),
                        'tender_organization' => fn(Builder $roleQuery) => $roleQuery->whereIn('id', $tenderOrganizationIds),
                        'other' => fn(Builder $roleQuery) => $roleQuery
                            ->whereNotIn('id', $buyerIds)
                            ->whereNotIn('id', $supplierIds)
                            ->whereNotIn('id', $tenderOrganizationIds),
                    };

                    $q->orWhere($roleQuery);
                }
            });
        }

        $sort = $filters['sort'] ?? 'name';
        $direction = ($filters['direction'] ?? 'asc') === 'desc' ? 'desc' : 'asc';

        return $query
            ->orderBy($sort, $direction)
            ->orderBy('id')
            ->paginate(
                (int) ($filters['per_page'] ?? 25),
                ['*'],
                'page',
                (int) ($filters['page'] ?? 1),
            );
    }

    public function getOrganizationKpis(): array
    {
        $buyerIds = Procedure::query()
            ->select('buyer_id')
            ->whereNotNull('buyer_id');

        $supplierIds = LotSupplier::query()->select('organization_id');

        $suppliers = Organization::whereIn('id', $supplierIds)->count();

        $smeSuppliers = Organization::whereIn('id', $supplierIds)
            ->whereIn('company_size', ['micro', 'small', 'medium', 'sme']) // skontroluj reálne hodnoty
            ->count();

        return [
            'total_organizations' => Organization::count(),
            'buyers' => Organization::whereIn('id', $buyerIds)->count(),
            'suppliers' => $suppliers,
            'countries' => Organization::whereNotNull('country')->distinct()->count('country'),
            'sme_suppliers_pct' => $suppliers > 0
                ? round($smeSuppliers / $suppliers * 100, 1)
                : null,
        ];
    }
}
