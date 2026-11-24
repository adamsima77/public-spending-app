<?php

declare(strict_types=1);

namespace App\Models;

use Carbon\CarbonInterface;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class SettledContract extends Model
{
    protected $fillable = [
        'notice_id',
        'notice_record_id',
        'contract_ref',
        'contract_number',
        'conclusion_date',
        'title',
        'contract_url',
        'tender_refs',
        'extra_fields',
    ];

    protected $casts = [
        'conclusion_date' => 'datetime',
        'notice_record_id' => 'integer',
        'tender_refs' => 'array',
        'extra_fields' => 'array',
    ];

    /** @return BelongsTo<Notice, $this> */
    public function notice(): BelongsTo
    {
        return $this->belongsTo(Notice::class, 'notice_record_id');
    }

    /** @return BelongsToMany<LotTender, $this> */
    public function tenders(): BelongsToMany
    {
        return $this->belongsToMany(
            LotTender::class,
            'settled_contract_tenders',
            'settled_contract_id',
            'lot_tender_id',
        );
    }

    public function scopeCurrent(Builder $query): Builder
    {
        return $query->whereHas('notice', fn(Builder $q) => $q->current());
    }

    public function scopeConcludedBetween(Builder $query, CarbonInterface $from, ?CarbonInterface $to = null): Builder
    {
        return $query
            ->where('conclusion_date', '>=', $from)
            ->when($to, fn(Builder $q) => $q->where('conclusion_date', '<', $to));
    }

    public function scopeWithContractUrl(Builder $query): Builder
    {
        return $query->whereNotNull('contract_url')->where('contract_url', '!=', '');
    }

    public function scopeForProcedure(Builder $query, int $procedureId): Builder
    {
        return $query->whereHas('notice', fn(Builder $q) => $q->where('procedure_id', $procedureId));
    }

    public function scopeForBuyer(Builder $query, int $buyerId): Builder
    {
        return $query->whereHas(
            'notice.procedure',
            fn(Builder $q) => $q->where('buyer_id', $buyerId),
        );
    }
}
