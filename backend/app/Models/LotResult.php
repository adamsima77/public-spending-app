<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class LotResult extends Model
{
    public const OUTCOME_AWARDED = 'selec-w';

    public const STAT_TOTAL_TENDERS = 'tenders';

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

    /** @return BelongsTo<ClNonAwardReason, $this> */
    public function nonAwardReason(): BelongsTo
    {
        return $this->belongsTo(ClNonAwardReason::class, 'non_award_reason', 'code');
    }

    /** @return HasMany<LotResultSubmissionStat, $this> */
    public function submissionStats(): HasMany
    {
        return $this->hasMany(LotResultSubmissionStat::class, 'lot_result_id');
    }

    public function tenders(): HasMany
    {
        return $this->hasMany(LotTender::class, 'lot_id', 'lot_id');
    }

    public function scopeCurrent(Builder $query): Builder
    {
        return $query->whereHas('notice', fn(Builder $q) => $q->current());
    }

    public function scopeWithOutcome(Builder $query): Builder
    {
        return $query->whereNotNull('award_outcome');
    }

    public function scopeAwarded(Builder $query): Builder
    {
        return $query->where('award_outcome', self::OUTCOME_AWARDED);
    }

    public function scopeWithBids(Builder $query): Builder
    {
        return $query->has('tenders');
    }

    public function totalTendersStat(): HasOne
    {
        return $this->hasOne(LotResultSubmissionStat::class, 'lot_result_id')
            ->where('category_code', self::STAT_TOTAL_TENDERS);
    }

    public function scopeWithSubmittedTenders(Builder $query): Builder
    {
        return $query->whereHas('totalTendersStat', fn(Builder $q) => $q->whereNotNull('count'));
    }
}
