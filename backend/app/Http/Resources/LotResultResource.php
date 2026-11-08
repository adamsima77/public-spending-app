<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class LotResultResource extends JsonResource
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
            'award_outcome' => $this->resource->award_outcome,
            'non_award_reason' => $this->resource->non_award_reason,
            'lowest_offer_value' => $this->resource->lowest_offer_value,
            'lowest_offer_currency' => $this->resource->lowest_offer_currency,
            'highest_offer_value' => $this->resource->highest_offer_value,
            'highest_offer_currency' => $this->resource->highest_offer_currency,
            'tender_refs' => $this->resource->tender_refs,
            'contract_refs' => $this->resource->contract_refs,
            'extra_fields' => $this->resource->extra_fields,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'lot' => new NoticeLotResource($this->whenLoaded('lot')),
            'award_outcome_definition' => new CodelistResource($this->whenLoaded('awardOutcome')),
            'non_award_reason_definition' => new CodelistResource($this->whenLoaded('nonAwardReason')),
            'submission_stats' => LotResultSubmissionStatResource::collection($this->whenLoaded('submissionStats')),
        ];
    }
}
