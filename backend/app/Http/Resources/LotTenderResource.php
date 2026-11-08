<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class LotTenderResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->resource->id,
            'notice_id' => $this->resource->notice_id,
            'notice_record_id' => $this->resource->notice_record_id,
            'lot_reference' => $this->resource->lot_reference,
            'lot_id' => $this->resource->lot_id,
            'tender_ref' => $this->resource->tender_ref,
            'tender_value' => $this->resource->tender_value,
            'tender_currency' => $this->resource->tender_currency,
            'tendering_party_ref' => $this->resource->tendering_party_ref,
            'rank' => $this->resource->rank,
            'subcontracting' => $this->resource->subcontracting,
            'extra_fields' => $this->resource->extra_fields,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'lot' => new NoticeLotResource($this->whenLoaded('lot')),
            'notice' => new NoticeResource($this->whenLoaded('notice')),
            'subcontracting_definition' => new CodelistResource($this->whenLoaded('subcontractingApplicability')),
            'organizations' => OrganizationResource::collection($this->whenLoaded('organizations')),
            'settled_contracts' => SettledContractResource::collection($this->whenLoaded('settledContracts')),
        ];
    }
}
