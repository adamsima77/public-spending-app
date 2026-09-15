<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Procedure extends Model
{
    protected $fillable = [
        'procedure_reference',
        'buyer_id',
        'procedure_type',
        'main_cpv',
        'total_value',
        'currency',
        'title',
        'description',
        'extra_fields'
    ];

    protected $casts = [
        'extra_fields' => 'array',
    ];
}
