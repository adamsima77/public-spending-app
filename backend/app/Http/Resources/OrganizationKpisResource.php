<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class OrganizationKpisResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'total_organizations' => (int) $this->resource['total_organizations'],
            'buyers' => (int) $this->resource['buyers'],
            'suppliers' => (int) $this->resource['suppliers'],
            'countries' => (int) $this->resource['countries'],
            'sme_suppliers_pct' => $this->resource['sme_suppliers_pct'] !== null
                ? (float) $this->resource['sme_suppliers_pct']
                : null,
        ];
    }
}
