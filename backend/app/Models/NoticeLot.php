<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

class NoticeLot extends Model
{
    protected $fillable = [
        'procedure_id',
        'lot_reference',
        'title',
        'description',
        'value',
        'currency',
        'main_cpv',
        'nuts_code',
        'place_of_performance',
        'award_criterion',
        'submission_deadline',
        'document_url',
        'detail_url',
        'duration_value',
        'duration_unit',
        'estimated_value',
        'estimated_currency',
        'eu_funded',
        'einvoicing_allowed',
        'eordering_allowed',
        'variants_allowed',
        'reserved_participation',
        'extra_fields',
    ];

    protected $casts = [
        'submission_deadline' => 'datetime',
        'value' => 'decimal:2',
        'estimated_value' => 'decimal:2',
        'duration_value' => 'integer',
        'eu_funded' => 'boolean',
        'einvoicing_allowed' => 'boolean',
        'eordering_allowed' => 'boolean',
        'extra_fields' => 'array',
    ];

    /** @return BelongsTo<Procedure, $this> */
    public function procedure(): BelongsTo
    {
        return $this->belongsTo(Procedure::class);
    }

    /** @return BelongsTo<CpvCode, $this> */
    public function cpvCode(): BelongsTo
    {
        return $this->belongsTo(CpvCode::class, 'main_cpv', 'code');
    }

    /** @return BelongsTo<NutCode, $this> */
    public function nutCode(): BelongsTo
    {
        return $this->belongsTo(NutCode::class, 'nuts_code', 'code');
    }

    /** @return BelongsToMany<Organization, $this, LotSupplier, 'pivot'> */
    public function suppliers(): BelongsToMany
    {
        return $this->belongsToMany(Organization::class, 'lot_suppliers', 'lot_id', 'organization_id')
            ->using(LotSupplier::class)
            ->withPivot('winning_amount')
            ->withTimestamps();
    }

    /** @return HasMany<LotResult, $this> */
    public function lotResults(): HasMany
    {
        return $this->hasMany(LotResult::class, 'lot_id');
    }

    /** @return HasMany<LotTender, $this> */
    public function tenders(): HasMany
    {
        return $this->hasMany(LotTender::class, 'lot_id');
    }
}
