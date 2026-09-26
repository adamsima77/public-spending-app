<?php

namespace App\Enums;

enum SystemType: string
{
    case AUDIT = "audit";
    case SECURITY = "security";
    case SYSTEM = "system";
}