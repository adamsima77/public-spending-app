<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class CpvCode extends Model
{
    protected $fillable = [
        'code',
        'name_sk',
        'level',
        'parent_code',
    ];

    protected $casts = [
        'level' => 'integer',
    ];

    /** @return BelongsTo<CpvCode, $this> */
    public function parent(): BelongsTo
    {
        return $this->belongsTo(CpvCode::class, 'parent_code', 'code');
    }

    /** @return HasMany<CpvCode, $this> */
    public function children(): HasMany
    {
        return $this->hasMany(CpvCode::class, 'parent_code', 'code');
    }

    /** @return HasMany<NoticeLot, $this> */
    public function noticeLots(): HasMany
    {
        return $this->hasMany(NoticeLot::class, 'main_cpv', 'code');
    }

    /** @return HasMany<Procedure, $this> */
    public function procedures(): HasMany
    {
        return $this->hasMany(Procedure::class, 'main_cpv', 'code');
    }
}
