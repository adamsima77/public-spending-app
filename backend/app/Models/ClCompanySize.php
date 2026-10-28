<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ClCompanySize extends Model
{
    public $incrementing = false;

    public $timestamps = false;

    protected $table = 'cl_company_sizes';

    protected $primaryKey = 'code';

    protected $keyType = 'string';

    protected $fillable = [
        'code',
        'label_sk',
    ];

    /** @return HasMany<Organization, $this> */
    public function organizations(): HasMany
    {
        return $this->hasMany(Organization::class, 'company_size', 'code');
    }
}
