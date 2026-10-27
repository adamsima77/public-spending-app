<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ClAwardOutcome extends Model
{
    use HasFactory;

    protected $table = 'cl_award_outcomes';

    protected $primaryKey = 'code';
    public $incrementing = false;
    protected $keyType = 'string';

    public $timestamps = false;

    protected $fillable = [
        'code',
        'label_sk',
    ];

    public function lotResults(): HasMany
    {
        return $this->hasMany(LotResult::class, 'award_outcome', 'code');
    }
}
