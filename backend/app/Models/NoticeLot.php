<?php

namespace App\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

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
        'extra_fields',
        'submission_deadline',
        'document_url',
        'detail_url',
        'procedure_id',
        'nuts_code',
        'main_cpv'
    ];

    protected $casts = [
        'extra_fields' => 'array',
    ];

    public function procedure(): BelongsTo
    {
        return $this->hasMany(Procedure::class);
    }
}
