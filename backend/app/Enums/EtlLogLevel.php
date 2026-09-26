<?php

namespace App\Enums;

enum SystemEvent: string
{
    case INFO = "info";
    case WARNING = "security";
    case ERROR = "system";
}