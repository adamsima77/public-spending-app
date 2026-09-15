<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class NutCode extends Model
{
    protected $fillable = [
        'code',
        'name_sk',
        'level',
        'parent_code',
    ];
}
