<?php

declare(strict_types=1);

namespace App\Enums;

enum EtlStatuses: string
{
    case PENDING = 'pending';
    case DOWNLOADING = 'downloading';
    case DOWNLOADED = 'downloaded';
    case FAILED = 'failed';
    case PARSED = 'parsed';
}
