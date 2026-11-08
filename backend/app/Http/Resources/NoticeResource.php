<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class NoticeResource extends JsonResource
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
            'notice_id' => $this->resource->notice_id,
            'notice_version' => $this->resource->notice_version,
            'form_type' => $this->resource->form_type,
            'notice_type' => $this->resource->notice_type,
            'legal_basis' => $this->resource->legal_basis,
            'title' => $this->resource->title,
            'issue_date' => $this->resource->issue_date,
            'published_at' => $this->resource->published_at,
            'is_latest' => $this->resource->is_latest,
            'extra_fields' => $this->resource->extra_fields,
            'procedure_id' => $this->resource->procedure_id,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'procedure' => new ProcedureResource($this->whenLoaded('procedure')),
            'form_type_definition' => new CodelistResource($this->whenLoaded('formType')),
            'notice_type_definition' => new CodelistResource($this->whenLoaded('noticeType')),
            'legal_basis_definition' => new CodelistResource($this->whenLoaded('legalBasis')),
            'lot_results' => LotResultResource::collection($this->whenLoaded('lotResults')),
            'lot_tenders' => LotTenderResource::collection($this->whenLoaded('lotTenders')),
            'settled_contracts' => SettledContractResource::collection($this->whenLoaded('settledContracts')),
        ];
    }
}
