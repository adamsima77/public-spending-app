<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Notice extends Model
{
    protected $fillable = [
        'notice_id',
        'notice_version',
        'form_type',
        'notice_type',
        'legal_basis',
        'dispatch_date',
        'title',
        'supersedes_id',
        'extra_fields'
    ];

    protected $casts = [
        'extra_fields' => 'array',
        'dispatch_date' => 'date',
    ];
}
