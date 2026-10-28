<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class NutCode extends Model
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

    /** @return BelongsTo<NutCode, $this> */
    public function parent(): BelongsTo
    {
        return $this->belongsTo(NutCode::class, 'parent_code', 'code');
    }

    /** @return HasMany<NutCode, $this> */
    public function children(): HasMany
    {
        return $this->hasMany(NutCode::class, 'parent_code', 'code');
    }

    /** @return HasMany<NoticeLot, $this> */
    public function noticeLots(): HasMany
    {
        return $this->hasMany(NoticeLot::class, 'nuts_code', 'code');
    }

    /** @return HasMany<Organization, $this> */
    public function organizations(): HasMany
    {
        return $this->hasMany(Organization::class, 'nuts_code', 'code');
    }

    /** @return HasMany<Procedure, $this> */
    public function procedures(): HasMany
    {
        return $this->hasMany(Procedure::class, 'nuts_code', 'code');
    }
}
