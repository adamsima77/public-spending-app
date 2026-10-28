<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Procedure extends Model
{
    protected $fillable = [
        'procedure_reference',
        'procedure_identifier',
        'buyer_id',
        'procedure_type',
        'contract_type',
        'main_cpv',
        'total_value',
        'currency',
        'nuts_code',
        'place_of_performance',
        'title',
        'description',
        'buyer_profile_url',
        'performance_note',
        'extra_fields',
    ];

    protected $casts = [
        'buyer_id' => 'integer',
        'total_value' => 'decimal:2',
        'extra_fields' => 'array',
    ];

    /** @return BelongsTo<Organization, $this> */
    public function buyer(): BelongsTo
    {
        return $this->belongsTo(Organization::class, 'buyer_id');
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

    /** @return HasMany<NoticeLot, $this> */
    public function noticeLots(): HasMany
    {
        return $this->hasMany(NoticeLot::class);
    }

    /** @return HasMany<Notice, $this> */
    public function notices(): HasMany
    {
        return $this->hasMany(Notice::class);
    }
}
