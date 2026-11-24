<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class SettledContractKpiResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'contracts' => [
                'total' => (int) $this->resource['contracts']['total'],
                'last_30' => (int) $this->resource['contracts']['last_30'],
                'prev_30' => (int) $this->resource['contracts']['prev_30'],
                'change_pct' => $this->resource['contracts']['change_pct'],
                'latest_conclusion' => $this->resource['contracts']['latest_conclusion'],
            ],
            'coverage' => [
                'with_url' => (int) $this->resource['coverage']['with_url'],
                'with_url_pct' => (float) $this->resource['coverage']['with_url_pct'],
                'with_tenders' => (int) $this->resource['coverage']['with_tenders'],
                'with_tenders_pct' => (float) $this->resource['coverage']['with_tenders_pct'],
                'with_tender_refs' => (int) $this->resource['coverage']['with_tender_refs'],
            ],
            'reach' => [
                'notices' => (int) $this->resource['reach']['notices'],
                'buyers' => (int) $this->resource['reach']['buyers'],
            ],
            'monthly' => $this->resource['monthly'],
        ];
    }
}
