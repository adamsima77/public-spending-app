<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Procedure extends Model
{
    use HasFactory;

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


    public function buyer(): BelongsTo
    {
        return $this->belongsTo(Organization::class, 'buyer_id');
    }

    public function cpvCode(): BelongsTo
    {
        return $this->belongsTo(CpvCode::class, 'main_cpv', 'code');
    }

    public function nutCode(): BelongsTo
    {
        return $this->belongsTo(NutCode::class, 'nuts_code', 'code');
    }

    public function noticeLots(): HasMany
    {
        return $this->hasMany(NoticeLot::class);
    }

    public function notices(): HasMany
    {
        return $this->hasMany(Notice::class);
    }
}
