<?php

namespace App\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Procedure extends Model
{
    protected $fillable = [
        'procedure_reference',
        'buyer_id',
        'procedure_type',
        'main_cpv',
        'total_value',
        'currency',
        'nuts_code',
        'title',
        'description',
        'buyer_profile_url',
        'extra_fields'
    ];

    protected $casts = [
        'extra_fields' => 'array',
    ];

    public function notices(): HasMany
    {
        return $this->hasMany(Notice::class);
    }

    public function noticeLots(): HasMany
    {
        return $this->hasMany(NoticeLot::class);
    }
}
