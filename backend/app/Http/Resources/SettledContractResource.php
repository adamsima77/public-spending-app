<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class SettledContractResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->resource->id,
            'notice_id' => $this->resource->notice_id,
            'notice_record_id' => $this->resource->notice_record_id,
            'contract_ref' => $this->resource->contract_ref,
            'contract_number' => $this->resource->contract_number,
            'conclusion_date' => $this->resource->conclusion_date,
            'title' => $this->resource->title,
            'contract_url' => $this->resource->contract_url,
            'tender_refs' => $this->resource->tender_refs,
            'extra_fields' => $this->resource->extra_fields,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'notice' => new NoticeResource($this->whenLoaded('notice')),
            'tenders' => LotTenderResource::collection($this->whenLoaded('tenders')),
        ];
    }
}
