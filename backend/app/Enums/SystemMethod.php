<?php

namespace App\Enums;

enum SystemMethod: string
{
    case POST = "POST";
    case PUT = "PUT";
    case DELETE = "DELETE";
    case GET = "GET";
    case PATCH = "PATCH";
    case OPTIONS = "OPTIONS";
}