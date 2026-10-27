<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ClCompanySize extends Model
{
    use HasFactory;

    protected $table = 'cl_company_sizes';

    protected $primaryKey = 'code';
    public $incrementing = false;
    protected $keyType = 'string';

    public $timestamps = false;

    protected $fillable = [
        'code',
        'label_sk',
    ];

    public function organizations(): HasMany
    {
        return $this->hasMany(Organization::class, 'company_size', 'code');
    }
}
