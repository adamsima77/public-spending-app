<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ProcedureResource extends JsonResource
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
            'procedure_reference' => $this->resource->procedure_reference,
            'procedure_identifier' => $this->resource->procedure_identifier,
            'source_order_id' => $this->resource->source_order_id,
            'buyer_id' => $this->resource->buyer_id,
            'procedure_type' => $this->resource->procedure_type,
            'contract_type' => $this->resource->contract_type,
            'main_cpv' => $this->resource->main_cpv,
            'estimated_value' => $this->resource->estimated_value,
            'currency' => $this->resource->currency,
            'nuts_code' => $this->resource->nuts_code,
            'place_of_performance' => $this->resource->place_of_performance,
            'title' => $this->resource->title,
            'description' => $this->resource->description,
            'buyer_profile_url' => $this->resource->buyer_profile_url,
            'performance_note' => $this->resource->performance_note,
            'extra_fields' => $this->resource->extra_fields,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'buyer' => new OrganizationResource($this->whenLoaded('buyer')),
            'procedure_type_definition' => new CodelistResource($this->whenLoaded('procedureType')),
            'contract_nature' => new CodelistResource($this->whenLoaded('contractNature')),
            'cpv_code' => new CpvCodeResource($this->whenLoaded('cpvCode')),
            'nut_code' => new NutCodeResource($this->whenLoaded('nutCode')),
            'notices' => NoticeResource::collection($this->whenLoaded('notices')),
            'notice_lots' => NoticeLotResource::collection($this->whenLoaded('noticeLots')),
        ];
    }
}
