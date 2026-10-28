<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Organization extends Model
{
    protected $fillable = [
        'cin',
        'tin',
        'name',
        'address',
        'street_name',
        'street_number',
        'phone',
        'town',
        'postal_code',
        'country',
        'nuts_code',
        'company_size',
        'extra_fields',
    ];

    protected $casts = [
        'extra_fields' => 'array',
    ];

    /** @return BelongsTo<NutCode, $this> */
    public function nutCode(): BelongsTo
    {
        return $this->belongsTo(NutCode::class, 'nuts_code', 'code');
    }

    /** @return HasMany<Procedure, $this> */
    public function procedures(): HasMany
    {
        return $this->hasMany(Procedure::class, 'buyer_id');
    }

    /** @return BelongsTo<ClCompanySize, $this> */
    public function companySize(): BelongsTo
    {
        return $this->belongsTo(ClCompanySize::class, 'company_size', 'code');
    }

    /** @return BelongsToMany<NoticeLot, $this, LotSupplier, 'pivot'> */
    public function suppliedLots(): BelongsToMany
    {
        return $this->belongsToMany(NoticeLot::class, 'lot_suppliers', 'organization_id', 'lot_id')
            ->using(LotSupplier::class)
            ->withPivot('winning_amount')
            ->withTimestamps();
    }
}
