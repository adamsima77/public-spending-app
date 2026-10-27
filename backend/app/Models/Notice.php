<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Notice extends Model
{
    use HasFactory;

    protected $fillable = [
        'notice_id',
        'notice_version',
        'form_type',
        'notice_type',
        'legal_basis',
        'title',
        'issue_date',
        'published_at',
        'is_latest',
        'extra_fields',
        'procedure_id',
    ];

    protected $casts = [
        'notice_version' => 'integer',
        'procedure_id' => 'integer',
        'issue_date' => 'datetime',
        'published_at' => 'datetime',
        'is_latest' => 'boolean',
        'extra_fields' => 'array',
    ];

    public function procedure(): BelongsTo
    {
        return $this->belongsTo(Procedure::class);
    }
}
