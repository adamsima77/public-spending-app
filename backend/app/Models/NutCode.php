<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class NutCode extends Model
{
    use HasFactory;

    protected $fillable = [
        'code',
        'name_sk',
        'level',
        'parent_code',
    ];

    protected $casts = [
        'level' => 'integer',
    ];

    public function parent(): BelongsTo
    {
        return $this->belongsTo(NutCode::class, 'parent_code', 'code');
    }

    public function children(): HasMany
    {
        return $this->hasMany(NutCode::class, 'parent_code', 'code');
    }

    public function noticeLots(): HasMany
    {
        return $this->hasMany(NoticeLot::class, 'nuts_code', 'code');
    }

    public function organizations(): HasMany
    {
        return $this->hasMany(Organization::class, 'nuts_code', 'code');
    }

    public function procedures(): HasMany
    {
        return $this->hasMany(Procedure::class, 'nuts_code', 'code');
    }
}
