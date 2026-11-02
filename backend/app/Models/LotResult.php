<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class LotResult extends Model
{
    protected $fillable = [
        'notice_id',
        'notice_record_id',
        'lot_reference',
        'lot_id',
        'award_outcome',
        'non_award_reason',
        'lowest_offer_value',
        'lowest_offer_currency',
        'highest_offer_value',
        'highest_offer_currency',
        'tender_refs',
        'contract_refs',
        'extra_fields',
    ];

    protected $casts = [
        'lot_id' => 'integer',
        'notice_record_id' => 'integer',
        'lowest_offer_value' => 'decimal:2',
        'highest_offer_value' => 'decimal:2',
        'tender_refs' => 'array',
        'contract_refs' => 'array',
        'extra_fields' => 'array',
    ];

    /** @return BelongsTo<NoticeLot, $this> */
    public function lot(): BelongsTo
    {
        return $this->belongsTo(NoticeLot::class, 'lot_id');
    }

    /** @return BelongsTo<Notice, $this> */
    public function notice(): BelongsTo
    {
        return $this->belongsTo(Notice::class, 'notice_record_id');
    }

    /** @return BelongsTo<ClAwardOutcome, $this> */
    public function awardOutcome(): BelongsTo
    {
        return $this->belongsTo(ClAwardOutcome::class, 'award_outcome', 'code');
    }

    /** @return HasMany<LotResultSubmissionStat, $this> */
    public function submissionStats(): HasMany
    {
        return $this->hasMany(LotResultSubmissionStat::class, 'lot_result_id');
    }
}
