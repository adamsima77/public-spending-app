<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class NoticeKpiResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        $notices = $this->resource['notices'];
        $lots = $this->resource['lots'];
        $competition = $this->resource['competition'];

        $noticesTotal = (int) $notices['total'];
        $noticesLast30 = (int) $notices['last_30'];
        $noticesPrev30 = (int) $notices['prev_30'];

        $lotsTotal = (int) $lots['lots'];
        $lotsTotalValue = (float) $lots['total_value'];
        $lotsAwarded = (int) $lots['awarded'];
        $lotsWithOutcome = (int) $lots['with_outcome'];
        $lotsEuFunded = (int) $lots['eu_funded'];
        $lotsEuKnown = (int) $lots['eu_known'];

        $competitionAvgBids = (float) $competition['avg_bids'];
        $competitionSingleBid = (int) $competition['single_bid'];
        $competitionLots = (int) $competition['lots'];

        return [
            'notices' => [
                'total' => $noticesTotal,
                'last_30_days' => $noticesLast30,
                'change_percent' => $this->change($noticesLast30, $noticesPrev30),
            ],
            'lots' => [
                'total' => $lotsTotal,
                'total_estimated_value' => round($lotsTotalValue, 2),
                'currency' => 'EUR',
            ],
            'award_rate' => [
                'awarded' => $lotsAwarded,
                'of' => $lotsWithOutcome,
                'percent' => $this->percent($lotsAwarded, $lotsWithOutcome),
            ],
            'competition' => [
                'avg_bids_per_lot' => round($competitionAvgBids, 1),
                'single_bid_lots' => $competitionSingleBid,
                'single_bid_percent' => $this->percent($competitionSingleBid, $competitionLots),
            ],
            'eu_funding' => [
                'eu_funded_lots' => $lotsEuFunded,
                'percent' => $this->percent($lotsEuFunded, $lotsEuKnown),
            ],
        ];
    }

    private function percent(int $part, int $total): ?float
    {
        return $total > 0 ? round($part / $total * 100, 1) : null;
    }

    private function change(int $current, int $previous): ?float
    {
        return $previous > 0 ? round(($current - $previous) / $previous * 100, 1) : null;
    }
}
