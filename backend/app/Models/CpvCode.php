<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CpvCode extends Model
{
    protected $fillable = [
        'code',
        'name_sk',
        'level',
        'parent_code'
    ];
}
