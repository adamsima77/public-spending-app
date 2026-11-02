<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class LotTender extends Model
{
    protected $fillable = [
        'notice_id',
        'notice_record_id',
        'lot_reference',
        'lot_id',
        'tender_value',
        'tender_currency',
        'tendering_party_ref',
        'rank',
        'subcontracting',
        'extra_fields',
    ];

    protected $casts = [
        'lot_id' => 'integer',
        'notice_record_id' => 'integer',
        'rank' => 'integer',
        'tender_value' => 'decimal:2',
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

    /** @return BelongsToMany<Organization, $this> */
    public function organizations(): BelongsToMany
    {
        return $this->belongsToMany(Organization::class, 'lot_tender_organizations');
    }

    /** @return BelongsToMany<SettledContract, $this> */
    public function settledContracts(): BelongsToMany
    {
        return $this->belongsToMany(
            SettledContract::class,
            'settled_contract_tenders',
            'lot_tender_id',
            'settled_contract_id',
        );
    }
}
