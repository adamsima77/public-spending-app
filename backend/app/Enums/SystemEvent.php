<?php

declare(strict_types=1);

namespace App\Enums;

enum SystemEvent: string
{
    case CREATED = 'created';
    case UPDATED = 'updated';
    case DELETED = 'deleted';
}
