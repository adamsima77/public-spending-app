<?php

declare(strict_types=1);

namespace App\Enums;

enum ContactEnum: string
{
    case RECEIVED = 'received';
    case REPLIED = 'replied';
}
