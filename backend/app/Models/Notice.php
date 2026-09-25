<?php

namespace App\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Notice extends Model
{
    protected $fillable = [
        'notice_id',
        'notice_version',
        'form_type',
        'notice_type',
        'legal_basis',
        'title',
        'supersedes_id',
        'contract_conclusion_date',
        'issue_date',
        'extra_fields',
        'procedure_id'
    ];

    protected $casts = [
        'extra_fields' => 'array'
    ];

    public function procedure(): BelongsTo 
    {
        return $this->belongsTo(Procedure::class);
    }
}
