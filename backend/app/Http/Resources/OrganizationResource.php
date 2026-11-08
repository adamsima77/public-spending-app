<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class OrganizationResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->resource->id,
            'cin' => $this->resource->cin,
            'tin' => $this->resource->tin,
            'name' => $this->resource->name,
            'address' => $this->resource->address,
            'street_name' => $this->resource->street_name,
            'street_number' => $this->resource->street_number,
            'phone' => $this->resource->phone,
            'town' => $this->resource->town,
            'postal_code' => $this->resource->postal_code,
            'country' => $this->resource->country,
            'nuts_code' => $this->resource->nuts_code,
            'company_size' => $this->resource->company_size,
            'extra_fields' => $this->resource->extra_fields,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'nut_code' => new CodelistResource($this->whenLoaded('nutCode')),
            'company_size_definition' => new CodelistResource($this->whenLoaded('companySize')),
        ];
    }
}
