<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class EtlStatus extends Model
{
    protected $fillable = [
        'name',
    ];

    /** @return HasMany<DownloadedFile, $this> */
    public function downloadedFiles(): HasMany
    {
        return $this->hasMany(DownloadedFile::class);
    }
}
