<?php

declare(strict_types=1);

namespace App\Models;

use Carbon\CarbonInterface;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Notice extends Model
{
    protected $fillable = [
        'notice_id',
        'notice_version',
        'form_type',
        'notice_type',
        'legal_basis',
        'title',
        'issue_date',
        'published_at',
        'is_latest',
        'extra_fields',
        'procedure_id',
    ];

    protected $casts = [
        'notice_version' => 'integer',
        'procedure_id' => 'integer',
        'issue_date' => 'datetime',
        'published_at' => 'datetime',
        'is_latest' => 'boolean',
        'extra_fields' => 'array',
    ];

    /** @return BelongsTo<Procedure, $this> */
    public function procedure(): BelongsTo
    {
        return $this->belongsTo(Procedure::class);
    }

    /** @return BelongsTo<ClFormType, $this> */
    public function formType(): BelongsTo
    {
        return $this->belongsTo(ClFormType::class, 'form_type', 'code');
    }

    /** @return BelongsTo<ClNoticeType, $this> */
    public function noticeType(): BelongsTo
    {
        return $this->belongsTo(ClNoticeType::class, 'notice_type', 'code');
    }

    /** @return BelongsTo<ClLegalBasis, $this> */
    public function legalBasis(): BelongsTo
    {
        return $this->belongsTo(ClLegalBasis::class, 'legal_basis', 'code');
    }

    /** @return HasMany<LotResult, $this> */
    public function lotResults(): HasMany
    {
        return $this->hasMany(LotResult::class, 'notice_record_id');
    }

    /** @return HasMany<LotTender, $this> */
    public function lotTenders(): HasMany
    {
        return $this->hasMany(LotTender::class, 'notice_record_id');
    }

    /** @return HasMany<SettledContract, $this> */
    public function settledContracts(): HasMany
    {
        return $this->hasMany(SettledContract::class, 'notice_record_id');
    }

    public function scopeCurrent(Builder $query): Builder
    {
        return $query->where('is_latest', true);
    }

    public function scopePublishedBetween(Builder $query, CarbonInterface $from, ?CarbonInterface $to = null): Builder
    {
        return $query
            ->where('published_at', '>=', $from)
            ->when($to, fn(Builder $q) => $q->where('published_at', '<', $to));
    }
}
