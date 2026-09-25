<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Organization extends Model
{
    protected $fillable = [
        'cin',
        'tin',
        'name',
        'address',
        'town',
        'postal_code',
        'country',
        'nuts_code',
        'phone',
        'street_number',
        'street_name',
        'extra_fields'
    ];
           
    protected $casts = [
        'extra_fields' => 'array',
    ];
}
