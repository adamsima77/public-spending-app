<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('organizations', function (Blueprint $table) {
            $table->id();
            $table->string('cin', 100)->nullable();
            $table->string('tin', 100)->nullable();
            $table->string('name')->nullable();
            $table->string('address')->nullable();
            $table->string('street_name')->nullable();
            $table->string('street_number')->nullable();
            $table->string('phone')->nullable();
            $table->string('town')->nullable();
            $table->string('postal_code', 20)->nullable();
            $table->string('country', 5)->nullable();
            $table->string('nuts_code', 10)->nullable();
            $table->string('company_size', 16)->nullable();
            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();

            $table->index('cin', 'organizations_cin_index');
            $table->index('tin', 'organizations_tin_index');
            $table->index('nuts_code');
            $table->index('company_size');

            $table->foreign('nuts_code')->references('code')->on('nut_codes')->nullOnDelete();
        });

        DB::statement("CREATE UNIQUE INDEX organizations_country_cin_unique ON organizations ((COALESCE(country, '')), cin) WHERE cin IS NOT NULL;");
        DB::statement("CREATE UNIQUE INDEX organizations_country_tin_unique ON organizations ((COALESCE(country, '')), tin) WHERE tin IS NOT NULL;");
    }

    public function down(): void
    {
        Schema::dropIfExists('organizations');
    }
};