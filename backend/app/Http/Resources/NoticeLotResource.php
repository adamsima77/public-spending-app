<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class NoticeLotResource extends JsonResource
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
            'procedure_id' => $this->resource->procedure_id,
            'lot_reference' => $this->resource->lot_reference,
            'title' => $this->resource->title,
            'description' => $this->resource->description,
            'estimated_value' => $this->resource->estimated_value,
            'estimated_currency' => $this->resource->estimated_currency,
            'main_cpv' => $this->resource->main_cpv,
            'nuts_code' => $this->resource->nuts_code,
            'place_of_performance' => $this->resource->place_of_performance,
            'award_criterion' => $this->resource->award_criterion,
            'submission_deadline' => $this->resource->submission_deadline,
            'document_url' => $this->resource->document_url,
            'detail_url' => $this->resource->detail_url,
            'duration_value' => $this->resource->duration_value,
            'duration_unit' => $this->resource->duration_unit,
            'eu_funded' => $this->resource->eu_funded,
            'eordering_allowed' => $this->resource->eordering_allowed,
            'epayment_allowed' => $this->resource->epayment_allowed,
            'einvoicing' => $this->resource->einvoicing,
            'variants_allowed' => $this->resource->variants_allowed,
            'reserved_execution' => $this->resource->reserved_execution,
            'reserved_participation' => $this->resource->reserved_participation,
            'framework_max_value' => $this->resource->framework_max_value,
            'framework_max_currency' => $this->resource->framework_max_currency,
            'extra_fields' => $this->resource->extra_fields,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'procedure' => new ProcedureResource($this->whenLoaded('procedure')),
            'cpv_code' => new CpvCodeResource($this->whenLoaded('cpvCode')),
            'nut_code' => new NutCodeResource($this->whenLoaded('nutCode')),
            'duration_unit_definition' => new CodelistResource($this->whenLoaded('durationUnit')),
            'award_criterion_type' => new CodelistResource($this->whenLoaded('awardCriterionType')),
            'reserved_execution_definition' => new CodelistResource($this->whenLoaded('reservedExecutionType')),
            'reserved_participation_definition' => new CodelistResource($this->whenLoaded('reservedParticipationType')),
            'einvoicing_permission' => new CodelistResource($this->whenLoaded('einvoicingPermission')),
            'variants_applicability' => new CodelistResource($this->whenLoaded('variantsApplicability')),
            'suppliers' => OrganizationResource::collection($this->whenLoaded('suppliers')),
            'lot_results' => LotResultResource::collection($this->whenLoaded('lotResults')),
            'tenders' => LotTenderResource::collection($this->whenLoaded('tenders')),
        ];
    }
}
