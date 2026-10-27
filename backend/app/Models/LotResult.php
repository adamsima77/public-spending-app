<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class LotResult extends Model
{
    use HasFactory;

    protected $fillable = [
        'notice_id',
        'lot_reference',
        'lot_id',
        'award_outcome',
        'non_award_reason',
        'lowest_offer_value',
        'lowest_offer_currency',
        'highest_offer_value',
        'highest_offer_currency',
        'tender_ref',
        'contract_ref',
        'extra_fields',
    ];

    protected $casts = [
        'lot_id' => 'integer',
        'lowest_offer_value' => 'decimal:2',
        'highest_offer_value' => 'decimal:2',
        'extra_fields' => 'array',
    ];

    public function lot(): BelongsTo
    {
        return $this->belongsTo(NoticeLot::class, 'lot_id');
    }

    public function awardOutcome(): BelongsTo
    {
        return $this->belongsTo(ClAwardOutcome::class, 'award_outcome', 'code');
    }

    public function submissionStats(): HasMany
    {
        return $this->hasMany(LotResultSubmissionStat::class, 'lot_result_id');
    }
}
