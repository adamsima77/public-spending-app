<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class NoticeLot extends Model
{
    protected $fillable = [
        'lot_reference',
        'title',
        'description',
        'value',
        'currency',
        'main_cpv',
        'nuts_code',
        'award_criterion',
        'extra_fields'
    ];

    protected $casts = [
        'extra_fields' => 'array',
    ];
}
