<?php

declare(strict_types=1);

namespace App\Models;

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
}
