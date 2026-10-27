<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SettledContract extends Model
{
    use HasFactory;

    protected $fillable = [
        'notice_id',
        'contract_number',
        'conclusion_date',
        'document_type',
        'contract_url',
        'tender_ref',
        'extra_fields',
    ];

    protected $casts = [
        'conclusion_date' => 'datetime',
        'extra_fields' => 'array',
    ];
}
