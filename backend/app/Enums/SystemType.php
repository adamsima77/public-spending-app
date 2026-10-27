<?php

declare(strict_types=1);

namespace App\Enums;

enum SystemType: string
{
    case AUDIT = 'audit';
    case SECURITY = 'security';
    case SYSTEM = 'system';
}
