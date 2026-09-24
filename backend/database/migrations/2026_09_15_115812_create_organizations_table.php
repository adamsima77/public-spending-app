<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('organizations', function (Blueprint $table) {
            $table->id();
            $table->string('cin', 100)->nullable();   // BT-501-Organization-Company-CIN (IČO)
            $table->string('tin', 100)->nullable();   // BT-501-Organization-Company-TIN (DIČ)
            $table->string('name')->nullable();                  // BT-500-Organization-Company
            $table->string('address')->nullable();               // Zložené z street_name + street_number + street_line2
            $table->string('street_name')->nullable();           // BT-510(a)-Organization-Company
            $table->string('street_number')->nullable();         // BT-510(b)-Organization-Company
            $table->string('phone')->nullable();                 // BT-503-Organization-Company
            $table->string('town')->nullable();                  // BT-513-Organization-Company
            $table->string('postal_code', 20)->nullable();       // BT-512-Organization-Company
            $table->string('country', 5)->nullable();            // BT-514-Organization-Company
            $table->string('nuts_code', 10)->nullable();         // BT-507-Organization-Company (Sídlo)
            $table->timestamps();
            $table->unique('cin');
            $table->jsonb('extra_fields')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('organizations');
    }
};