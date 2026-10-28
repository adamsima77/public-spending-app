<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class EtlLog extends Model
{
    public const CREATED_AT = 'created_at';

    public const UPDATED_AT = null;

    public $timestamps = false;

    protected $fillable = [
        'file_id',
        'level',
        'message',
        'context',
    ];

    /**
     * Vzťah k stiahnutému súboru (DownloadedFile)
     */
    /** @return BelongsTo<DownloadedFile, $this> */
    public function file(): BelongsTo
    {
        return $this->belongsTo(DownloadedFile::class, 'file_id');
    }
}
